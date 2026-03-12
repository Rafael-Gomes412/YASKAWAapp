import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Importation complète depuis Excel vers le modèle Product Yaskawa'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='Forcer une catégorie (ex: Motion). Sinon lu depuis la colonne Category du fichier.'
        )

    def handle(self, *args, **options):
        file_path     = options['excel_file']
        category_name = options.get('category')

        from Yaskawa_app_bckend.models import Product, Category

        try:
            # 1. Chargement du fichier
            df = pd.read_excel(file_path)

            # 2. Nettoyage des noms de colonnes
            df.columns = [str(c).strip() for c in df.columns]
            self.stdout.write(f"Colonnes détectées : {list(df.columns)}")

            # 3. Catégorie forcée (optionnel)
            forced_category = None
            if category_name:
                forced_category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'slug': slugify(category_name)}
                )
                self.stdout.write(f"Catégorie forcée : {category_name}")

            count = 0
            for index, row in df.iterrows():

                # ModelCode obligatoire
                m_code = str(row.get('ModelCode', '')).strip()
                if not m_code or m_code == 'nan':
                    continue

                # Gestion catégorie
                if forced_category:
                    category_obj = forced_category
                else:
                    c_name = str(row.get('Category', 'Non classé')).strip()
                    category_obj, _ = Category.objects.get_or_create(
                        name=c_name,
                        defaults={'slug': slugify(c_name)}
                    )

                # Création ou mise à jour — mapping identique à la vue web
                Product.objects.update_or_create(
                    model_code=m_code,
                    defaults={
                        'category':        category_obj,
                        'numero_SAP':      str(row.get('SAPNo',       '') or '').strip(),
                        'product_type':    str(row.get('Product',     '') or '').strip(),
                        'features':        str(row.get('Attribute1',  '') or '').strip(),
                        'specification':   str(row.get('Attribute2',  '') or '').strip(),
                        'compatible':      str(row.get('Attribute3',  '') or '').strip(),
                        'usable_with':     str(row.get('Attribute4',  '') or '').strip(),
                        'compat_range_1':  str(row.get('Attribute5',  '') or '').strip(),
                        'compat_range_2':  str(row.get('Attribute6',  '') or '').strip(),
                        'compat_range_3':  str(row.get('Attribute7',  '') or '').strip(),
                        'compat_range_4':  str(row.get('Attribute8',  '') or '').strip(),
                        'compat_range_5':  str(row.get('Attribute9',  '') or '').strip(),
                        'compat_range_6':  str(row.get('Attribute10', '') or '').strip(),
                        'compat_range_7':  str(row.get('Attribute11', '') or '').strip(),
                        'compat_range_8':  str(row.get('Attribute12', '') or '').strip(),
                        'compat_range_9':  str(row.get('Attribute13', '') or '').strip(),
                        'compat_range_10': str(row.get('Attribute14', '') or '').strip(),
                        'compat_range_11': str(row.get('Attribute15', '') or '').strip(),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Succès : {count} produits importés/mis à jour !'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur critique : {e}'))