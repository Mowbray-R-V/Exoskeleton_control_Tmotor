import numpy as np
from matplotlib import pyplot as plt


def theta_5(w, t, phi, shift):

    a0 = 10.14
    a1 = 14.1
    b1 = 6.004
    a2 = 1.857  
    b2 = -3.034
    a3 = -1.008
    b3 = -1.078

    return shift * (shift * a0 + a1*np.cos(t*w + phi) + b1*np.sin(t*w + phi) +
                    a2*np.cos(2*t*w + phi) + b2*np.sin(2*t*w + phi) + a3*np.cos(3*t*w + phi) + b3*np.sin(3*t*w + phi)) * np.pi/180


def omega_5(w, t, phi, shift):

    a0 = 10.14
    a1 = 14.1
    b1 = 6.004
    a2 = 1.857
    b2 = -3.034
    a3 = -1.008
    b3 = -1.078

    return shift * w * (-a1*np.sin(t*w+phi) + b1*np.cos(t*w+phi) - 2 * a2 * np.sin(2*t*w+phi) + 2 * b2*np.cos(2*t*w+phi) - 3 * a3 * np.sin(3*t*w+phi) + 3 * b3 * np.cos(3*t*w+phi)) * np.pi/180


def theta_6(w, t, phi, shift):

    a0 = -16.45
    a1 = 3.503
    b1 = 25.09
    a2 = 8.535
    b2 = 10.42
    a3 = 3.325
    b3 = 2.333
    a4 = 0.3077
    b4 = 1.366

    return (shift * (shift * a0 + a1*np.cos(t*w+phi) + b1*np.sin(t*w+phi) + a2*np.cos(2*t*w+phi) + b2*np.sin(2*t*w+phi) + a3*np.cos(3*t*w+phi) + b3*np.sin(3*t*w+phi) +
                     a4*np.cos(4*t*w+phi) + b4*np.sin(4*t*w+phi)) * np.pi/180)


def omega_6(w, t, phi, shift):

    a0 = -16.45
    a1 = 3.503
    b1 = 25.09
    a2 = 8.535
    b2 = 10.42
    a3 = 3.325
    b3 = 2.333
    a4 = 0.3077
    b4 = 1.366

    return (shift * w * (-a1*np.sin(t*w+phi) + b1*np.cos(t*w+phi) -
                         2 * a2 * np.sin(2*t*w+phi) + 2 * b2*np.cos(2*t*w+phi) - 3 * a3 * np.sin(3*t*w+phi) + 3 * b3 * np.cos(3*t*w+phi) +
                         - 4 * a4*np.sin(4*t*w+phi) + 4 * b4*np.cos(4*t*w+phi)) * np.pi/180)


def theta_6_rel(w, t, phi, shift):

    a0 = -16.45
    a1 = 3.503
    b1 = 25.09
    a2 = 8.535
    b2 = 10.42
    a3 = 3.325
    b3 = 2.333
    a4 = 0.3077
    b4 = 1.366

    return (shift * (shift * a0 + a1*np.cos(t*w+phi) + b1*np.sin(t*w+phi) + a2*np.cos(2*t*w+phi) + b2*np.sin(2*t*w+phi) + a3*np.cos(3*t*w+phi) + b3*np.sin(3*t*w+phi) +
                     a4*np.cos(4*t*w+phi) + b4*np.sin(4*t*w+phi)) * np.pi/180) - theta_5(w, t, phi, shift)


def omega_6_rel(w, t, phi, shift):

    a0 = -16.45
    a1 = 3.503
    b1 = 25.09
    a2 = 8.535
    b2 = 10.42
    a3 = 3.325
    b3 = 2.333
    a4 = 0.3077
    b4 = 1.366

    return (shift * w * (-a1*np.sin(t*w+phi) + b1*np.cos(t*w+phi) -
                         2 * a2 * np.sin(2*t*w+phi) + 2 * b2*np.cos(2*t*w+phi) - 3 * a3 * np.sin(3*t*w+phi) + 3 * b3 * np.cos(3*t*w+phi) +
                         - 4 * a4*np.sin(4*t*w+phi) + 4 * b4*np.cos(4*t*w+phi)) * np.pi/180 + omega_5(w, t, phi, shift))


if __name__ == '__main__':
    times = np.linspace(0, 10, 1000)
    plt.plot(times, 180/np.pi * theta_6(2, times, 0))
    plt.plot(times, 180/np.pi * theta_6(2, times, np.pi))

    plt.legend(["KNEE", "KNEESHIFT"])

    plt.show()
