import pandas as pd
from django.core.management.base import BaseCommand
from Yaskawa_app_bckend.models import Product, Compatibility

class Command(BaseCommand):
    help = 'Importation ultra-rapide des 24k liaisons de compatibilité'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)

    def handle(self, *args, **options):
        file_path = options['excel_file']
        
        try:
            # 1. Chargement de l'Excel en mémoire
            df = pd.read_excel(file_path)
            df.columns = [str(c).strip() for c in df.columns]
            
            # 2. Mise en CACHE des produits (on charge tout en 1 seule requête)
            self.stdout.write("Mise en cache des produits...")
            # On crée un dictionnaire { 'CODE': Objet_Produit }
            product_cache = {p.model_code: p for p in Product.objects.all()}
            
            # 3. Récupération des liaisons existantes pour éviter les doublons
            self.stdout.write("Vérification des doublons existants...")
            existing_links = set(
                Compatibility.objects.values_list('source_product__model_code', 'compatible_product__model_code')
            )

            new_compatibilities = []
            errors = 0

            # 4. Traitement ultra-rapide en mémoire
            self.stdout.write(f"Traitement de {len(df)} lignes...")
            for index, row in df.iterrows():
                m1 = str(row.get('ModelCode1', '')).strip()
                m2 = str(row.get('ModelCode2', '')).strip()

                # On vérifie si les deux produits existent dans notre cache mémoire
                p1 = product_cache.get(m1)
                p2 = product_cache.get(m2)

                if p1 and p2:
                    # On vérifie si le lien n'existe pas déjà (en mémoire aussi)
                    if (m1, m2) not in existing_links:
                        new_compatibilities.append(
                            Compatibility(
                                source_product=p1,
                                compatible_product=p2,
                                relation_type='Compatible'
                            )
                        )
                        # On l'ajoute au set pour éviter les doublons à l'intérieur du même Excel
                        existing_links.add((m1, m2))
                else:
                    errors += 1

            # 5. Insertion groupée (Bulk Create) : 1 seule requête pour des milliers de lignes
            if new_compatibilities:
                self.stdout.write(f"Insertion de {len(new_compatibilities)} nouvelles liaisons...")
                Compatibility.objects.bulk_create(new_compatibilities, batch_size=1000)
            
            self.stdout.write(self.style.SUCCESS(
                f"Terminé ! {len(new_compatibilities)} liens créés. {errors} codes introuvables."
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur critique : {e}"))