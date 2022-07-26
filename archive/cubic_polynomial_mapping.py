import numpy as np


def cubic_polynomial_mapping():
    # To find the cubic polinomial mapping:
    # y = ax^3 + bx^2 + cx + d
    # y'(50) = midPointSlope
    # y(50)  = midPointValue
    # y(100) = 100
    # y(1)   = 1
    # We have 4 equations and 4 variables: a,b,c,d
    # This is a linear system of equations:
    # 0 = 3*50**2*a+2*50*b+c
    # 100 = 100**3*a+100**2*b+100*c+d
    # 50 = 50**3*a+50**2*b+50*c+d
    # 1 = a+b+c+d
    # Let us arrange this in matrix form:
    midPointSlope = 0
    A = np.array([[3 * 50 ** 2, 2 * 50, 1, 0],
                  [50 ** 3, 50 ** 2, 50, 1],
                  [100 ** 3, 100 ** 2, 100, 1],
                  [1, 1, 1, 1]])

    # Find the 4 coefficients - a,b,c,d:
    midPointValue = 50
    coefficients = np.linalg.inv(A).dot([midPointSlope, midPointValue, 100, 1])
    return coefficients
