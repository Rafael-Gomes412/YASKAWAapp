import time
import pandas as pd
from django.core.management.base import BaseCommand
from Yaskawa_app_bckend.models import Product


class Command(BaseCommand):
    help = 'Mise à jour du stock depuis un fichier Excel (présence = en stock)'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Chemin vers le fichier Excel (.xlsx)'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default=0,
            help='Nom ou index de la feuille Excel (défaut: première feuille)'
        )
        parser.add_argument(
            '--col-code',
            type=str,
            default='ModelCode',
            help='Colonne contenant le code produit (défaut: ModelCode)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule sans écrire en base'
        )

    def handle(self, *args, **options):
        file_path = options['excel_file']
        sheet     = options['sheet']
        col_code  = options['col_code']
        dry_run   = options['dry_run']

        start = time.time()

        if dry_run:
            self.stdout.write(self.style.WARNING("⚠  MODE DRY-RUN — aucune écriture en base"))

        # ── 1. Chargement Excel ────────────────────────────────────────────
        self.stdout.write(f"📂 Chargement : {file_path}")
        try:
            df = pd.read_excel(file_path, sheet_name=sheet)
            df.columns = [str(c).strip() for c in df.columns]
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ Fichier introuvable : {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Impossible de lire le fichier : {e}"))
            return

        if col_code not in df.columns:
            self.stdout.write(self.style.ERROR(
                f"❌ Colonne '{col_code}' introuvable. Colonnes disponibles : {list(df.columns)}"
            ))
            return

        self.stdout.write(f"   → {len(df)} lignes trouvées")

        # Extraction des codes uniques non vides
        stock_codes = set()
        for val in df[col_code].dropna():
            code = str(val).strip()
            if code and code != 'nan':
                stock_codes.add(code)

        self.stdout.write(f"   → {len(stock_codes)} codes uniques dans l'Excel")

        # ── 2. Cache produits ──────────────────────────────────────────────
        self.stdout.write("🗄  Mise en cache des produits...")
        all_products = list(Product.objects.only('id', 'model_code', 'numero_SAP', 'in_stock'))

        by_model_code = {p.model_code: p for p in all_products}
        by_sap        = {p.numero_SAP: p for p in all_products if p.numero_SAP}

        self.stdout.write(f"   → {len(by_model_code)} produits en base")

        # ── 3. Traitement ──────────────────────────────────────────────────
        self.stdout.write("⚙  Calcul des changements...")

        to_in_stock  = []
        to_out_stock = []
        not_found    = []

        # Produits présents dans l'Excel → in_stock = True
        for code in stock_codes:
            product = by_model_code.get(code) or by_sap.get(code)
            if product:
                if not product.in_stock:
                    product.in_stock = True
                    to_in_stock.append(product)
            else:
                not_found.append(code)

        # Produits absents de l'Excel → in_stock = False
        for p in all_products:
            in_excel = (p.model_code in stock_codes) or (p.numero_SAP in stock_codes)
            if not in_excel and p.in_stock:
                p.in_stock = False
                to_out_stock.append(p)

        # ── 4. Écriture en base ────────────────────────────────────────────
        if not dry_run:
            if to_in_stock:
                Product.objects.bulk_update(to_in_stock, ['in_stock'], batch_size=500)
            if to_out_stock:
                Product.objects.bulk_update(to_out_stock, ['in_stock'], batch_size=500)

        elapsed = round(time.time() - start, 2)

        # ── 5. Rapport ─────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write("─" * 50)
        self.stdout.write(self.style.SUCCESS(f"✅ Import terminé en {elapsed}s"))
        self.stdout.write(f"   • Passés en stock      : {len(to_in_stock)}")
        self.stdout.write(f"   • Passés hors stock    : {len(to_out_stock)}")
        self.stdout.write(f"   • Codes introuvables   : {len(not_found)}")

        if not_found:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("⚠  Codes absents de la base (30 premiers) :"))
            for code in not_found[:30]:
                self.stdout.write(f"   ? {code}")
            if len(not_found) > 30:
                self.stdout.write(f"   ... et {len(not_found) - 30} autres")