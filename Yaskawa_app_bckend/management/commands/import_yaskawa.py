import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Importation complète depuis Excel vers le modèle Product Yaskawa'

    def add_arguments(self, parser):
        # Permet de passer le nom du fichier en argument (ex: TestBDD1.xlsx)
        parser.add_argument('excel_file', type=str)

    def handle(self, *args, **options):
        file_path = options['excel_file']
        # Import local pour éviter les problèmes de chargement au démarrage
        from Yaskawa_app_bckend.models import Product, Category
        
        try:
            # 1. Chargement du fichier
            df = pd.read_excel(file_path)
            
            # 2. Nettoyage des noms de colonnes pour éviter les erreurs de frappe (KeyError)
            df.columns = [str(c).strip() for c in df.columns]
            
            self.stdout.write(f"Colonnes détectées : {list(df.columns)}")

            count = 0
            for index, row in df.iterrows():
                # On récupère le ModelCode (obligatoire)
                m_code = str(row.get('ModelCode', '')).strip()
                
                # Si la ligne est vide ou sans code, on passe à la suivante
                if not m_code or m_code == 'nan':
                    continue

                # 3. Gestion de la Catégorie
                c_cate = str(row.get('Category', 'Non classé')).strip()
                category_obj, _ = Category.objects.get_or_create(
                    name=c_cate,
                    defaults={'slug': slugify(c_cate)}
                )

                # 4. Création ou Mise à jour du produit
                # On utilise les noms de champs EXACTS de ton models.py
                Product.objects.update_or_create(
                    model_code=m_code,
                    defaults={
                        'category': category_obj,
                        'numero_SAP': str(row.get('NoSAP', '')).strip(),
                        'product_type': str(row.get('Product', '')).strip(),
                        'features': str(row.get('Features', '')).strip(),
                        'specification': str(row.get('Specification', '')).strip(),
                        'usable_with': str(row.get('Usable_with', '')).strip(),
                        # 'compatible' est dans ton modèle mais pas encore utilisé ici
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Succès : {count} produits importés/mis à jour !'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur critique lors de l\'import : {e}'))