# Overview
A software to calculate consumed resource (quantum memory occupation duration), especially due to entanglement purification.
Users can input threshold of fidelity to execute entanglement swapping, between neighboring nodes, between intermediate nodes, and between end nodes.
The output is separated, consumed resource at intermediate nodes, consumed resource at end nodes, and consumed resource in total.

# How to use
To run single setting, execute

```
% python3 End2EndPurification/e2ep.py input/template_input.json
```

To run in batch, execute

```
%python3 End2EndPurification/executor.py End2EndPurification/parameters_template.py
```

# Contribution
Please read the CLA below carefully before submitting your contribution.

[https://www.mercari.com/cla/](https://www.mercari.com/cla/)

# Licence
Copyright 2017 Mercari, Inc.

Licensed under the MIT License.

