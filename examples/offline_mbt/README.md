# Offline model-bases testing example

This folder contains example of offline MBT

Files:
* [offline_mbt.py](offline_mbt.py) contains simple calculator model and somo. Executing this generates tests in a file.
* [sut_calculator.py](sut_calculator.py) simulates system under testing in this case

## How to use?

Generate test cases
```bash
python offline_mbt.py
```

Execute test cases
```bash
pytest generated_test.py
```