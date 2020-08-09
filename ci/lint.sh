echo "**** pylint ****"
pylint ./timelapse || exit $?
echo "**** black ****"
black ./timelapse --check --diff || exit $?
echo "**** mypy ****"
mypy ./timelapse --ignore-missing-imports || exit $?
echo "**** SUCCESS ****"