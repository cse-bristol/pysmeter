# pysmeter

A package for estimating the Heat Transfer Coefficient of a domestic building using smart meter data.

## Background

**SMETER** = **S**mart **M**eter **E**nabled **T**hermal **E**fficiency **R**ating

This package was borne out of an innovation competition run by BEIS (the UK Government Department for Business, Energy and Industrial Strategy) whose aim was to find unobtrusive and cost-effective ways of determining the HTC of a domestic building using smart meter data.

The team at the [Centre for Sustainable Energy](https://cse.org.uk) developed a machine learning model which uses the following data series collected from the dwelling (all measurements are taken half-hourly):

- Average indoor temperature*
- Outdoor temperature**
- Gas kWh
- Electricity kWh

\* Readings can be taken with any good temperature logger. Loggers should be placed in as many rooms as possible and the mean taken across all rooms.

\*\* A single logger should be placed outside the dwelling within a [Stevenson screen](https://en.wikipedia.org/wiki/Stevenson_screen) to shield it from direct sunlight.

For more info on the physical setup of sensors, see the [guidance](#sensor-placement-guidance).

From these data the model produces an estimate of the HTC of the building, as would be found by performing a co-heating test. The model itself is an ensemble of convolutional neural networks built with Tensorflow.

## Installation

Install with pip:
```
pip install pysmeter
```

It is recommended that you use a virtual env. Python >= 3.6 ships with venv in the standard library, so you can do:
```
python3 -m venv /path/to/new/virtual/environment
```
```
cd /path/to/new/virtual/environment
```
```
source bin/activate
```
```
pip install pysmeter
```

The install does not include the model files themselves, as they are very large (~300MB). These need to be downloaded separately after installation:
```
python3 -m pysmeter.download_model
```

This downloads the model files to `/usr/share/smeter-models` (Linux) or `/usr/local/share/smeter-models` (Mac).
You may need to run this command as root.

## Usage

### Python module

It is generally expected that you will use pysmeter within an existing Python project. The package exposes a single function, `pysmeter.model.predict`, which makes an HTC prediction based on the input array. The input array can be either two-dimensional (if there is only one building) or three-dimensional (more than one building). The dimensions are:

 - [_number of houses_ x] _timesteps_ x _channels_

There are always four channels: indoor temp, outdoor temp, gas, elec.

The number of timesteps should be at least 1008 (i.e. 3 weeks worth of half hours). The current model does not work with variable length input, but there are two versions of the model, one which has been trained on 3 weeks of data and one which has been trained on 4 weeks of data. If the supplied input array contains between 3 and 4 weeks of data then it will be truncated down to the first three weeks. If the supplied input array contains more than 4 weeks of data then it will be truncated down to the first four weeks.

The predict function returns a list of predictions for each of the datasets it is given, where each prediction is a tuple containing the prediction itself, the lower bound and the upper bound.

```python
import pysmeter.model as smeter

X = <code to make input array>

# Make the predictions
predictions = smeter.predict(X)

for htc, lower, upper in predictions:
    print(f"HTC: {htc} | Lower bound: {lower} | Upper bound: {upper}")
```

Here is a more illustrative example where we assume that we have two buildings whose data series are stored in the files `data1.csv` and `data2.csv`, where the csv files have headers `indoor, outdoor, gas, elec`.
```python
import csv
import numpy as np
import pysmeter.model as smeter

def _read_data(file_path):
    """Reads data from file and returns 4 lists containing the data for each channel."""
    indoor, outdoor, gas, elec = [], [], [], []

    with open(file_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            indoor.append(float(row["indoor"]))
            outdoor.append(float(row["outdoor"]))
            gas.append(float(row["gas"]))
            elec.append(float(row["elec"]))

    return indoor, outdoor, gas, elec

x1 = _read_data("data1.csv")
x2 = _read_data("data2.csv")

# Put the data into a numpy array and make it the right shape
X = np.array([x1, x2]).transpose((0, 2, 1))

# Make the predictions
predictions = smeter.predict(X)

for htc, lower, upper in predictions:
    print(f"HTC: {htc} | Lower bound: {lower} | Upper bound: {upper}")
```

### CLI

There is also a command line interface to the progamme which lets you run the SMETER model on data from a csv file.

The csv file must have four columns with readings for each of the four channels (average indoor temperature, outdoor temperature, gas kWh, elec kWh).

It will be assumed that each row corresponds to a single datetime and that time entries are 30 min apart.
If a datetime column is present, it will do no harm, but it will be ignored by the program.

The expected column names are: `indoor, outdoor, gas, elec`.

They can be in any order. If your csv has different column names you can declare them using the -i, -o, -g, -e options
(see example below).

Simple usage:

    pysmeter /path/to/csv/file.csv

With optional csv column headers:

    pysmeter /path/to/csv/file.csv -i 'Indoor temperature' -o 'Outdoor temperature'
    pysmeter /path/to/csv/file.csv -g 'Gas'
    pysmeter /path/to/csv/file.csv -e 'Electricity Usage (kWh)'

## Limitations

The primary limitation of the model is that it has been trained on simulated data. Due to the high cost of performing co-heating tests, very few have been performed on UK houses - fewer still where the required sensor and smart meter data has been collected. As a result, the training set was generated from simulations of houses based on [English Housing Survey](https://www.gov.uk/government/collections/english-housing-survey) data, using the [EnergyPlus](https://energyplus.net/) building energy modelling programme. Labels for the data were generated by creating simulated coheating tests in EnergyPlus.

A related limitation is that the SMETER model has only been validated on a small number of real test cases. The results are shown in the table below:

| True HTC | Predicted HTC | Prediction +/- |
| -------- | ------------- | -------------- |
| 194      | 196           | 33             |
| 159      | 176           | 33             |
| 155      | 176           | 34             |
| 269      | 447           | 35             |
| 194      | 157           | 35             |
| 244      | 214           | 35             |


The six test houses were semi-detached houses with gas central heating, located in the north of England.

It should be noted that the SMETER model is only designed to work with houses heated by a gas central heating system, since these make up the majority of the UK housing stock.


## Sensor placement guidance

When placing the temperature sensors in the dwelling, it is important to adhere to the following guidance. Failure to do so will affect the accuracy of the HTC prediction.

- Temperature sensors should be placed in as many rooms of the house as is feasible. The stairwell/landing can be considered to be a single room as it is one continuous thermal zone.
- The ideal sensor position is the exact centre of the room, although this is likely to be impossible in most cases. The next best place is halfway up a wall, or placed on a bookcase, say.
- Sensors should not be placed near windows, sources of heat or in places where they will receive direct sunlight. They should also not be placed in places where they are likely to be moved, knocked off a perch or mistaken for a toy by children.
- It is recommended that you number each of the sensors, either with a sticker or with permanent marker, and make a map of the house showing all the sensor locations.
- The outside sensor can be placed anywhere close to the house, e.g. the front or back garden. It _must_ be placed within a Stevenson screen to shield it from direct sunlight.

For more detailed guidance, see [https://smeter.cse.org.uk/guidance](https://smeter.cse.org.uk/guidance). We have also provided a template for noting sensor placement in MS Word format at [https://smeter.cse.org.uk/guidance/SMETER-sensor-placement-template.docx](https://smeter.cse.org.uk/guidance/SMETER-sensor-placement-template.docx).
