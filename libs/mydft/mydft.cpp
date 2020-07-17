#include <Python.h>
// Shared definitions
#include <cmath>
#include <vector>
# define M_PI           3.14159265358979323846  /* pi */
using std::size_t;
using std::vector;


/*
 * Computes the discrete Fourier transform (DFT) of the given complex vector.
 * All the array arguments must have the same length.
 */
#include <complex>
using std::complex;
using std::exp;
vector<complex<double> > computeDft(const vector<complex<double> >& input) {
    vector<complex<double> > output;
    size_t n = input.size();
    for (size_t k = 0; k < n; k++) {  // For each output element
        complex<double> sum(0.0, 0.0);
        for (size_t t = 0; t < n; t++) {  // For each input element
            double angle = 2 * M_PI * t * k / n;
            sum += input[t] * exp(-angle);
        }
        output.push_back(sum);
    }
    return output;
}


/*
 * (Alternate implementation using only real numbers.)
 * Computes the discrete Fourier transform (DFT) of the given complex vector.
 * All the array arguments must have the same length.
 */
using std::cos;
using std::sin;
PyObject* PycomputeDft(PyObject*, PyObject* Args)/*(const vector<double>& inreal, const vector<double>& inimag,
    vector<double>& outreal, vector<double>& outimag) */{
    PyObject* Fs = PyFloat_FromDouble(44100);
    PyObject* Inputcomplex;
    PyObject* output;
    PyObject* BasicFreq = PyFloat_FromDouble(440);
    if (!PyArg_UnpackTuple(Args,"(tuple(X),float(sampleFreq=44100),float(basicFreq=440))",1,3,&Inputcomplex,&Fs,&BasicFreq))
        return NULL;
    double ftable[] =  { 8.17579891564368, 8.661957218027224, 9.177023997418956, 9.722718241314997, 10.300861153527153, 10.913382232281338, 11.56232570973854, 12.249857374429629, 12.978271799373248, 13.749999999999961, 14.56761754744027, 15.433853164253836, 16.35159783128737, 17.323914436054462, 18.354047994837927, 19.445436482630008, 20.60172230705432, 21.82676446456269, 23.124651419477093, 24.499714748859272, 25.95654359874651, 27.499999999999936, 29.135235094880553, 30.867706328507687, 32.70319566257476, 34.64782887210894, 36.70809598967587, 38.89087296526004, 41.20344461410866, 43.6535289291254, 46.249302838954215, 48.99942949771857, 51.91308719749305, 54.9999999999999, 58.270470189761134, 61.7354126570154, 65.40639132514954, 69.2956577442179, 73.41619197935177, 77.7817459305201, 82.40688922821735, 87.30705785825084, 92.49860567790847, 97.99885899543719, 103.82617439498615, 109.99999999999987, 116.54094037952235, 123.4708253140309, 130.8127826502992, 138.59131548843592, 146.83238395870364, 155.56349186104032, 164.81377845643482, 174.6141157165018, 184.99721135581706, 195.9977179908745, 207.65234878997242, 219.99999999999986, 233.08188075904482, 246.94165062806192, 261.6255653005985, 277.18263097687196, 293.66476791740746, 311.1269837220808, 329.62755691286986, 349.2282314330038, 369.99442271163434, 391.99543598174927, 415.3046975799451, 440.0, 466.1637615180899, 493.8833012561241, 523.2511306011974, 554.3652619537443, 587.3295358348153, 622.253967444162, 659.2551138257401, 698.456462866008, 739.988845423269, 783.9908719634989, 830.6093951598906, 880.0000000000003, 932.3275230361802, 987.7666025122486, 1046.502261202395, 1108.7305239074888, 1174.6590716696307, 1244.5079348883241, 1318.5102276514804, 1396.9129257320162, 1479.9776908465383, 1567.981743926998, 1661.2187903197814, 1760.000000000001, 1864.6550460723606, 1975.5332050244976, 2093.0045224047904, 2217.4610478149784, 2349.3181433392624, 2489.0158697766497, 2637.020455302962, 2793.825851464034, 2959.9553816930784, 3135.963487853998, 3322.4375806395647, 3520.000000000004, 3729.310092144724, 3951.066410048998, 4186.009044809583, 4434.92209562996, 4698.6362866785275, 4978.031739553302, 5274.040910605927, 5587.651702928071, 5919.91076338616, 6271.926975707999, 6644.875161279134, 7040.000000000013, 7458.6201842894525, 7902.132820098001, 8372.018089619172, 8869.844191259925, 9397.27257335706, 9956.06347910661, 10548.08182121186, 11175.303405856148, 11839.821526772326, 12543.853951416006 };
    if(!PyTuple_Check(Inputcomplex))
        return NULL;
    output = PyTuple_New(128);
    size_t n = PyTuple_Size(Inputcomplex);
    double fs = PyFloat_AsDouble(Fs);
    double basicfreq = PyFloat_AsDouble(BasicFreq);
    //int fs = 44100;
    for (size_t k = 0; k < 128; k++) {  // For each output element
        double sumreal = 0;
        double sumimag = 0;
        for (size_t t = 0; t < n; t++) {  // For each input element
            double thisfreq = ftable[k]*basicfreq/440.0;
            double angle = 2 * M_PI * t * thisfreq / fs;
            PyObject* fthisreal = PyTuple_GetItem(Inputcomplex, t);
            double thisreal = PyFloat_AsDouble(fthisreal);//PyComplex_RealAsDouble( PyTuple_GetItem(Inputcomplex,t));
            double thisimag = 0;//PyComplex_ImagAsDouble(PyTuple_GetItem(Inputcomplex,t));
            sumreal += thisreal * cos(angle) + thisimag * sin(angle);
            sumimag += -thisreal * sin(angle) + thisimag * cos(angle);
        }
        
        PyTuple_SetItem( output,k,PyComplex_FromDoubles(sumreal,sumimag));
        //outreal[k] = sumreal;
        //outimag[k] = sumimag;
    }
    Py_DECREF(Inputcomplex);
    //_CrtDumpMemoryLeaks();
    return output;
    
}



PyObject* PycomputeIDft(PyObject*, PyObject* Args)/*(const vector<double>& inreal, const vector<double>& inimag,
    vector<double>& outreal, vector<double>& outimag) */ {
    PyObject* Fs = PyFloat_FromDouble(44100);
    PyObject* Inputcomplex;
    PyObject* output;
    PyObject* BasicFreq = PyFloat_FromDouble(440);
    PyObject* Framesamp;
    PyObject* Currentframe = PyFloat_FromDouble(0);
    if (!PyArg_UnpackTuple(Args, "(tuple(X),float(sampleFreq=44100),float(basicFreq=440),int(framesamp=?),int(currentframe=0))", 1, 5, &Inputcomplex, &Fs, &BasicFreq, &Framesamp, &Currentframe))
        return NULL;
    double ftable[] = { 8.17579891564368, 8.661957218027224, 9.177023997418956, 9.722718241314997, 10.300861153527153, 10.913382232281338, 11.56232570973854, 12.249857374429629, 12.978271799373248, 13.749999999999961, 14.56761754744027, 15.433853164253836, 16.35159783128737, 17.323914436054462, 18.354047994837927, 19.445436482630008, 20.60172230705432, 21.82676446456269, 23.124651419477093, 24.499714748859272, 25.95654359874651, 27.499999999999936, 29.135235094880553, 30.867706328507687, 32.70319566257476, 34.64782887210894, 36.70809598967587, 38.89087296526004, 41.20344461410866, 43.6535289291254, 46.249302838954215, 48.99942949771857, 51.91308719749305, 54.9999999999999, 58.270470189761134, 61.7354126570154, 65.40639132514954, 69.2956577442179, 73.41619197935177, 77.7817459305201, 82.40688922821735, 87.30705785825084, 92.49860567790847, 97.99885899543719, 103.82617439498615, 109.99999999999987, 116.54094037952235, 123.4708253140309, 130.8127826502992, 138.59131548843592, 146.83238395870364, 155.56349186104032, 164.81377845643482, 174.6141157165018, 184.99721135581706, 195.9977179908745, 207.65234878997242, 219.99999999999986, 233.08188075904482, 246.94165062806192, 261.6255653005985, 277.18263097687196, 293.66476791740746, 311.1269837220808, 329.62755691286986, 349.2282314330038, 369.99442271163434, 391.99543598174927, 415.3046975799451, 440.0, 466.1637615180899, 493.8833012561241, 523.2511306011974, 554.3652619537443, 587.3295358348153, 622.253967444162, 659.2551138257401, 698.456462866008, 739.988845423269, 783.9908719634989, 830.6093951598906, 880.0000000000003, 932.3275230361802, 987.7666025122486, 1046.502261202395, 1108.7305239074888, 1174.6590716696307, 1244.5079348883241, 1318.5102276514804, 1396.9129257320162, 1479.9776908465383, 1567.981743926998, 1661.2187903197814, 1760.000000000001, 1864.6550460723606, 1975.5332050244976, 2093.0045224047904, 2217.4610478149784, 2349.3181433392624, 2489.0158697766497, 2637.020455302962, 2793.825851464034, 2959.9553816930784, 3135.963487853998, 3322.4375806395647, 3520.000000000004, 3729.310092144724, 3951.066410048998, 4186.009044809583, 4434.92209562996, 4698.6362866785275, 4978.031739553302, 5274.040910605927, 5587.651702928071, 5919.91076338616, 6271.926975707999, 6644.875161279134, 7040.000000000013, 7458.6201842894525, 7902.132820098001, 8372.018089619172, 8869.844191259925, 9397.27257335706, 9956.06347910661, 10548.08182121186, 11175.303405856148, 11839.821526772326, 12543.853951416006 };
    if (!PyTuple_Check(Inputcomplex))
        return NULL;
    double currentframe = PyFloat_AsDouble(Currentframe);
    double framesamp = PyFloat_AsDouble(Framesamp);
    output = PyTuple_New((long)framesamp);
    size_t n = framesamp;
    double fs = PyFloat_AsDouble(Fs);
    double basicfreq = PyFloat_AsDouble(BasicFreq);

    //int fs = 44100;
    for (size_t k = 0; k < framesamp; k++) {  // For each output element
        double sumreal = 0;
        double sumimag = 0;
        for (size_t t = 0; t < 128; t++) {  // For each input element
            double thisfreq = ftable[t] * basicfreq / 440.0;
            double angle = 2 * M_PI * (k+currentframe) * thisfreq / fs;
            PyObject* fthisreal = PyTuple_GetItem(Inputcomplex, t);
            double thisreal = PyFloat_AsDouble(fthisreal);//PyComplex_RealAsDouble( PyTuple_GetItem(Inputcomplex,t));
            double thisimag = 0;//PyComplex_ImagAsDouble(PyTuple_GetItem(Inputcomplex,t));
            sumreal += thisreal * cos(angle) - thisimag * sin(angle);
            sumimag += thisreal * sin(angle) + thisimag * cos(angle);
        }

        PyTuple_SetItem(output, k, PyComplex_FromDoubles(sumreal / 128, sumimag / 128));
        //outreal[k] = sumreal;
        //outimag[k] = sumimag;
    }
    Py_DECREF(Inputcomplex);
    //_CrtDumpMemoryLeaks();
    return output;

}


static PyMethodDef mydft_methods[] = {
    // The first property is the name exposed to Python, fast_tanh, the second is the C++
    // function name that contains the implementation.
    { "dft128", (PyCFunction)PycomputeDft, METH_VARARGS, nullptr },
    { "idft128", (PyCFunction)PycomputeIDft, METH_VARARGS, nullptr },
    // Terminate the array with an object containing nulls.
    { nullptr, nullptr, 0, nullptr }
};

static PyModuleDef mydft_module = {
    PyModuleDef_HEAD_INIT,
    "mydft",                        // Module name to use with Python import statements
    "Faster DFT using naive method.",  // Module description
    0,
    mydft_methods                   // Structure that defines the methods of the module
};

PyMODINIT_FUNC PyInit_mydft() {
    return PyModule_Create(&mydft_module);
}
PyMODINIT_FUNC PyInit_mydftmodule() {
    return PyModule_Create(&mydft_module);
}