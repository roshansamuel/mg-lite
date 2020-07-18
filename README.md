# MG-Lite - Multigrid Tutorial with Python

MG-Lite is a multigrid solver written in Python.
It solves a very simple one-dimensional Poisson equation to demonstrate the working of the multigrid V-cycle.
The solver is written in a single Python file titled ``mgLite.py``

## Installing MG-Lite

To install ``MG-Lite``, you need to first clone the git repository into your local machine

`git clone https://github.com/roshansamuel/mg-lite.git`

``MG-Lite`` is compatible with Python3, and can be executed by one of the following commands at the root folder of the solver, in the terminal.

`./mgLite.py`

or

`python mgLite.py`

Please make sure that the following Python modules are installed before executing the solver.

* ``numpy`` - All array manipulations are performed using NumPy
* ``matplotlib`` - Results from the solver are plotted using the ``matplotlib`` library

## License

``MG-Lite`` is an open-source package made available under the New BSD License.

## References

Below is a list of useful articles that explains the multigrid-method used by ``MG-Lite``

### Articles on multi-grid methods

1. http://math.mit.edu/classes/18.086/2006/am63.pdf
2. http://www.mgnet.org/mgnet-tuts.html
