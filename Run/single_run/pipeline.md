# pipeline completo

python imports/books/pipeline.py

# ver todos los pasos sin ejecutar nada

python imports/books/pipeline.py --list

# un solo paso (útil para debuggear)

python imports/books/pipeline.py --step "2_clean/gr_books"

# solo SQL, sin llamar a la API (corridas rápidas después de la primera)

python imports/books/pipeline.py --skip-enrich

# forzar re-enriquecimiento aunque no haya nuevos pendientes

python imports/books/pipeline.py --force-enrich
