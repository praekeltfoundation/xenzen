manage="${VENV}/bin/python ${INSTALLDIR}/xenzen/manage.py"

$manage migrate
$manage collectstatic --noinput
