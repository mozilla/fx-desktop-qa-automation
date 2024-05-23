result_file="test_results.log"

for i in {1..100}
do
  pytest tests/form_autofill/test_enable_disable_autofill.py

  if [ $? -eq 0 ]; then
    echo "Iteration $i: pass" >> "$result_file"
  else
    echo "Iteration $i: fail" >> "$result_file"
  fi
done