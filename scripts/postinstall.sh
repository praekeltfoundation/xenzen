manage="${VENV}/bin/python ${INSTALLDIR}/xenzen/manage.py"

$manage syncdb --noinput --no-initial-data --migrate
$manage collectstatic --noinput
