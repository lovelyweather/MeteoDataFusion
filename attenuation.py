# -*- coding: utf-8 -*-
"""
edited by haiqin chen, in 2022/11/24
source: https://github.com/wradlib/wradlib/blob/main/wradlib/atten.py
"""

import logging
import numpy as np
from scipy import interpolate, ndimage

logger = logging.getLogger("attcorr")

def correct_attenuation_hb(
    gateset,
    coefficients={"a": 1.67e-4, "b": 0.7, "gate_length": 1.0},
    mode="except",
    thrs=59.0,
):
    """Gate-by-Gate attenuation correction according to \
    :cite:`Hitschfeld1954`
    Parameters
    ----------
    gateset : :py:class:`numpy:numpy.ndarray`
        multidimensional array. The range gates (over which iteration has to
        be performed) are supposed to vary along
        the *last* dimension so, e.g., for a set of `l` radar images stored in
        polar form with `m` azimuths and `n` range-bins the input array's
        shape can be either (l,m,n) or (m,l,n)
        data has to be provided in decibel representation of reflectivity [dBZ]
    a : float
        proportionality factor of the k-Z relation (:math:`k=a \\cdot Z^{b}`).
        Per default set to 1.67e-4.
    b : float
        exponent of the k-Z relation ( :math:`k=a \\cdot Z^{b}` ). Per default
        set to 0.7.
    gate_length : float
        length of a range gate [km]. Per default set to 1.0.
    mode : str
        controls how the function reacts, if the sum of signal and attenuation
        exceeds the threshold ``thrs``
        Possible values:
        - 'warn' : emit a warning through the module's logger but continue
          execution
        - 'zero' : set offending gates to 0.0
        - 'nan' : set offending gates to nan
        - 'except': raise an AttenuationOverflowError exception
        Any other mode will also raise the Exception.
    thrs : float
        threshold, for the sum of attenuation and signal, which is considered
        implausible.
    Returns
    -------
    pia : :py:class:`numpy:numpy.ndarray`
        Array with the same shape as ``gateset`` containing the calculated
        attenuation [dB] for each range gate.
    Raises
    ------
    :exc:`wradlib.atten.AttenuationOverflowError`
    Examples
    --------
    See :ref:`/notebooks/attenuation/wradlib_attenuation.ipynb#\
Hitschfeld-and-Bordan`.
    """
    a = coefficients["a"]
    b = coefficients["b"]
    gate_length = coefficients["gate_length"]
    gateset = np.where(np.isnan(gateset), -999, gateset)

    pia = np.empty(gateset.shape)
    pia[..., 0] = 0.0
    ksum = 0.0

    # multidimensional version
    # assumes that iteration is only along the last dimension
    # (i.e. range gates) all other dimensions are calculated simultaneously
    # to gain some speed
    for gate in range(gateset.shape[-1] - 1):
        # calculate k in dB/km from k-Z relation
        # c.f. Krämer2008(p. 147)
        k = a * (10.0 ** ((gateset[..., gate] + ksum) / 10.0)) ** b * 2.0 * gate_length

        ksum += k
        # k = 10**(log10(a)+0.1*bin*b)
        # dBkn = 10*math.log10(a) + (bin+ksum)*b + 10*math.log10(2*gate_length)
        pia[..., gate + 1] = pia[..., gate] + k
        
        # stop-criterion, if corrected reflectivity is larger than 59 dBZ
        overflow = (gateset[..., gate + 1] + ksum) > thrs
        if np.any(overflow):
            if mode == "warn":
                logger.warning(f"corrected signal over threshold ({thrs:3.1f})")
            elif mode == "nan":
                pia[..., gate + 1][overflow] = np.nan
            elif mode == "zero":
                pia[..., gate + 1][overflow] = 0.0
            else:
                raise Exception("AttenuationOverflowError")
    #pia = np.where(np.isnan(pia), 0, pia)
    return pia

def constraint_dbz(gateset, pia, thrs_dbz):
    """Constraint callback function for correct_attenuation_constrained.
    Selects beams, in which at least one pixel exceeds ``thrs_dbz`` [dBZ].
    """
    return np.max(gateset + pia, axis=-1) > thrs_dbz

def constraint_pia(gateset, pia, thrs_pia):
    """Constraint callback function for correct_attenuation_constrained.
    Selects beams, in which the path integrated attenuation exceeds
    ``thrs_pia``.
    """
    return np.max(pia, axis=-1) > thrs_pia

def _sector_filter(mask, min_sector_size):
    """
    Calculate an array of same shape as mask, which is set to 1 in case of \
    at least min_sector_size adjacent values, otherwise it is set to 0.
    mask: stores beam index which exceeding all thresholds. array，0表示满足阈值条件，1表示不满足。
    min_sector_size: 在不符合约束条件的情况下，用于计算衰减的相邻波束的数量.
    """

    kernela = np.ones([1] * (mask.ndim - 1) + [min_sector_size]) # (1, mask.ndim - 1, min_sector_size)
    kernelb = np.ones((min_sector_size,))
    forward_origin = -(min_sector_size - (min_sector_size // 2)) + min_sector_size % 2
    backward_origin = (min_sector_size - (min_sector_size // 2)) - 1
    forward_sum = ndimage.correlate1d(
        mask.astype(np.int_), kernelb, axis=-1, mode="wrap", origin=forward_origin
    )
    backward_sum = ndimage.correlate1d(
        mask.astype(np.int_), kernelb, axis=-1, mode="wrap", origin=backward_origin
    )
    forward_corners = forward_sum == min_sector_size
    backward_corners = backward_sum == min_sector_size
    forward_large_sectors = np.zeros_like(mask)
    backward_large_sectors = np.zeros_like(mask)
    for iii in range(mask.shape[0]):
        forward_large_sectors[iii] = ndimage.binary_dilation(
            forward_corners[iii], kernela[0], origin=forward_origin
        ).astype(int)
        backward_large_sectors[iii] = ndimage.binary_dilation(
            backward_corners[iii], kernela[0], origin=backward_origin
        ).astype(int)

    return forward_large_sectors | backward_large_sectors

def calc_attenuation_forward(gateset, a=1.67e-4, b=0.7, gate_length=1.0):
    """Gate-by-Gate forward correction as described in :cite:`Kraemer2008`
    Parameters
    ----------
    gateset : :class:`numpy:numpy.ndarray`
        Multidimensional array, where the range gates (over which iteration has
        to be performed) are supposed to vary along the last array-dimension.
        Data has to be provided in decibel representation of reflectivity
        [dBZ].
    a : float
        proportionality factor of the k-Z relation (:math:`k=a \\cdot Z^{b}`).
        Per default set to 1.67e-4.
    b : float
        exponent of the k-Z relation ( :math:`k=a \\cdot Z^{b}` ). Per default
        set to 0.7.
    gate_length : float
        length of a range gate [km]. Per default set to 1.0.
    Returns
    -------
    pia : :class:`numpy:numpy.ndarray`
        Array with the same shape as ``gateset`` containing the calculated path
        integrated attenuation [dB] for each range gate.
    """
    gateset = np.where(np.isnan(gateset), -999, gateset)
    pia = np.zeros(gateset.shape)
    for gate in range(gateset.shape[-1] - 1):
        k = (
            a
            * idecibel(gateset[..., gate] + pia[..., gate]) ** b
            * 2.0
            * gate_length
        )
        pia[..., gate + 1] = pia[..., gate] + k
    pia = np.where(np.isnan(pia), 0, pia)
    return pia

def _interp_atten(pia, invalidbeams):
    """Interpolate reference pia of most distant rangebin of small invalid
    sectors as a prerequisite for the backward calculation of attenuation.
    """
    # Build an spatial equidistant array for interpolation of the ahead and
    # behind extended temporary pia-array for handling invalid sectors
    # overlapping the seam of the radarcircle.
    x = np.arange(3 * pia.shape[1])

    for i in range(pia.shape[0]):
        sub_invalid = invalidbeams[i, :]
        sub_pia = pia[i, :, -1]
        # Build the extended bool-array with the invalid sectors.
        extended_invalid = np.concatenate([sub_invalid] * 3)
        # Build the extended pia-array.
        extended_pia = np.concatenate([sub_pia] * 3)
        # Build interpolation class.
        intp = interpolate.interp1d(
            x[~extended_invalid], extended_pia[~extended_invalid], kind="linear"
        )
        # Interpolate where sectors are invalid.
        pia[i, sub_invalid, -1] = intp(x[pia.shape[1] : 2 * pia.shape[1]][sub_invalid])

def bisect_reference_attenuation(
    gateset,
    pia_ref,
    a_max=1.67e-4,
    a_min=2.33e-5,
    b_start=0.7,
    gate_length=1.0,
    mode="difference",
    thrs=0.25,
    max_iterations=10,
):
    """Find the optimal attenuation coefficients for a gateset to achieve a \
    given reference attenuation using a the forward correction algorithm in \
    combination with the bisection method.
    Parameters
    ----------
    gateset : :class:`numpy:numpy.ndarray`
        Multidimensional array, where the range gates (over which iteration has
        to be performed) are supposed to vary along the last array-dimension.
        Data has to be provided in decibel representation of reflectivity
        [dBZ].
    pia_ref : :class:`numpy:numpy.ndarray`
        Array of the same number of dimensions as ``gateset``, but the size of
        the last dimension is 1, as it constitutes the reference pia [dB] of
        the last range gate of every beam.
    a_max : float
        Upper bound of the bisection interval within the linear coefficient a
        of the k-Z relation has to be. ( :math:`k=a \\cdot Z^{b}` ).
        Per default set to 1.67e-4.
    a_min : float
        Lower bound of the bisection interval within the linear coefficient a
        of the k-Z relation has to be. ( :math:`k=a \\cdot Z^{b}` ).
        Per default set to 2.33e-5.
    b_start : float
        Initial value for exponential coefficient of the k-Z relation
        ( :math:`k=a \\cdot Z^{b}` ). This value will be lowered incremental
        by 0.01 if no solution was found within the bisection interval of
        ``a_max`` and ``a_min`` within the number of given iterations
        ``max_iterations``.
        Per default set to 0.7.
    gate_length : float
        Radial length of a range gate [km].
        Per default set to 1.0.
    mode : str
        {‘ratio’ or ‘difference’}
        Kind of tolerance of calculated pia in relation to reference pia.
        Per default set to 'difference'.
    thrs : float
        Value of the tolerance to stop bisection iteration successful. It is
        recommended to choose 0.05 for ratio ``mode`` and 0.25 for difference
        ``mode``, which means a deviation tolerance of 5% or 0.25 dB,
        respectively.
        Per default set to 0.25.
    max_iterations : int
        Number of bisection iteration before the exponential coefficient b of
        the k-Z relation will be decreased and the bisection starts again.
        Per default set to 10.
    Returns
    -------
    pia : :class:`numpy:numpy.ndarray`
        Array with the same shape as ``gateset`` containing the calculated path
        integrated attenuation [dB] for each range gate.
    a_mid : :class:`numpy:numpy.ndarray`
        Array with the same shape as ``pia_ref`` containing the finally used
        linear k-Z relation coefficient a for successful pia calculation.
    b : :class:`numpy:numpy.ndarray`
        Array with the same shape as ``pia_ref`` containing the finally used
        exponential k-Z relation coefficient b for successful pia calculation.
    """
    # Prepare arrays of initial k-Z relation coefficients for each beam.
    a_hi = np.ones(pia_ref.shape) * a_max  # np.repeat(a_max, pia_ref.shape)
    a_lo = np.ones(pia_ref.shape) * a_min  # np.repeat(a_min, pia_ref.shape)
    b = np.ones(pia_ref.shape) * b_start  # np.repeat(b_start, pia_ref.shape)
    pia = np.empty_like(gateset)
    iteration_count = 0

    # Iterate until upper and lower bounds of linear k-Z relation coefficients
    # for pia calculation are the same.
    while not np.all(a_hi == a_lo):
        a_mid = (a_hi + a_lo) / 2
        pia = calc_attenuation_forward(gateset, a_mid, b, gate_length)
        # Find indices where calculated and reference pia sufficiently match
        if mode == "difference":
            overshoot = (pia[..., -1] - pia_ref) > thrs
            undershoot = (pia[..., -1] - pia_ref) < -thrs
            hit = (np.abs(pia[..., -1] - pia_ref)) < thrs
        elif mode == "ratio":
            overshoot = ((pia[..., -1] - pia_ref) / pia_ref) > thrs
            undershoot = ((pia[..., -1] - pia_ref) / pia_ref) < -thrs
            hit = (np.abs(pia[..., -1] - pia_ref) / pia_ref) < thrs
        else:
            raise Exception("Unknown mode type " + mode + ".")
        # Define new bounds of linear k-Z relation coefficient for over- and
        # undershooting pia calculations.
        a_hi[overshoot] = a_mid[overshoot]
        a_lo[undershoot] = a_mid[undershoot]
        a_hi[hit] = a_mid[hit]
        a_lo[hit] = a_mid[hit]
        iteration_count += 1
        # Change exponential k-Z relation coefficient in case of maximum
        # iterations for linear k-Z relation coefficient are reached.
        if iteration_count > max_iterations:
            b[overshoot] -= 0.01
            b[undershoot] += 0.01
    return pia, a_mid, b

def correct_attenuation_constrained(
    gateset,
    a_max=1.67e-4,
    a_min=2.33e-5,
    n_a=4,
    b_max=0.7,
    b_min=0.65,
    n_b=6,
    gate_length=1.0,
    constraints=None,
    constraint_args=None,
    sector_thr=10,
):
    """
    整体的思路是，先给一个a和b的初值进行衰减订正，如果订正后的数值超过了阈值，比如说反射率太强了超过59 dBZ，这样的径向
    如果很多，那就调整系数重新来一次，直到满足条件为止。系数调整的策略是有a_max逐步降低到a_min，b_max逐渐降低到b_min，
    降低的步长由n_a和n_b决定。
    逐门订正，空间复杂度是原来的n_a*n_b倍。
    Gate-by-Gate attenuation correction based on the iterative approach of \
    :cite:`Kraemer2008` and :cite:`Jacobi2016` with a generalized and \
    scalable number of constraints.
    Differing from the original approach, the method for addressing
    small sectors which conflict with the constraints is based on a bisection
    forward calculating method, and not on backwards attenuation calculation.
    Parameters
    ----------
    gateset : :class:`numpy:numpy.ndarray`
        Multidimensional array, where the range gates (over which iteration has
        to be performed) are supposed to vary along the last array-dimension
        and the azimuths are supposed to vary along the next to last
        array-dimension.
        Data has to be provided in decibel representation of reflectivity
        [dBZ].
    a_max : float
        Initial value for linear coefficient of the k-Z relation
        ( :math:`k=a \\cdot Z^{b}` ).
        Per default set to 1.67e-4.
    a_min : float
        Minimal allowed linear coefficient of the k-Z relation
        ( :math:`k=a \\cdot Z^{b}` ) in the downwards iteration of 'a' in case
        of breaching one of thresholds ``constr_args`` of the optional
        conditions ``constraints``.
        Per default set to 2.33e-5.
    n_a : int
        Number of iterations from ``a_max`` to ``a_min``.
        Per default set to 4.
    b_max : float
        Initial value for exponential coefficient of the k-Z relation
        ( :math:`k=a \\cdot Z^{b}` ).
        Per default set to 0.7.
    b_min : float
        Minimal allowed exponential coefficient of the k-Z relation
        ( :math:`k=a \\cdot Z^{b}` ) in the downwards iteration of 'b' in case
        of breaching one of thresholds ``constr_args`` of the optional
        conditions ``constraints`` and the linear coefficient 'a' has already
        reached the lower limit ``a_min``.
        Per default set to 0.65.
    n_b : int
        Number of iterations from ``b_max`` to ``b_min``.
        Per default set to 6.
    gate_length : float
        Radial length of a range gate [km].
        Per default set to 1.0.
    constraints : list
        List of constraint functions. The signature of these functions has to
        be constraint_function(`gateset`, `k`, `*constr_args`). Their return
        value must be a boolean array of shape gateset.shape[:-1] set to True
        for beams, which do not fulfill the constraint.
    constraint_args : list
        List of lists, which are to be passed to the individual constraint
        functions using the `*args` mechanism
        (len(constr_args) == len(constraints)).
    sector_thr : int
        Number of adjacent beams, for which in case of breaching the
        constraints the attenuation with downward iterated ``a`` and ``b`` -
        parameters is recalculated. For more narrow sectors the integrated
        attenuation of the last gate is interpolated and used as reference
        for the recalculation.
        在不符合上述约束条件的情况下，用于计算衰减的相邻波束的数量
    Returns
    -------
    pia : :class:`numpy:numpy.ndarray`
        Array with the same shape as ``gateset`` containing the calculated path
        integrated attenuation [dB] for each range gate.
    Examples
    --------
    Implementing the original Hitschfeld & Bordan (1954) algorithm with
    otherwise default parameters::
        from wradlib.atten import *
        pia = correct_attenuation_constrained(gateset, a_max=8.e-5,
                                              b_max=0.731, n_a=1, n_b=1,
                                              gate_length=1.0)
    Implementing the basic Kraemer algorithm::
        pia = atten.correct_attenuation_constrained(gateset, a_max=1.67e-4,
                                                    a_min=2.33e-5, n_a=100,
                                                    b_max=0.7, b_min=0.65,
                                                    n_b=6, gate_length=1.,
                                                    constraints=
                                                    [wrl.atten.constraint_dbz],
                                                    constraint_args=[[59.0]])
    Implementing the PIA algorithm by Jacobi et al.::
        pia = atten.correct_attenuation_constrained(gateset, a_max=1.67e-4,
                                                    a_min=2.33e-5, n_a=100,
                                                    b_max=0.7, b_min=0.65,
                                                    n_b=6, gate_length=1.,
                                                    constraints=
                                                    [wrl.atten.constraint_dbz,
                                                    wrl.atten.constraint_pia],
                                                    constraint_args=
                                                    [[59.0],[20.0]])
    """
    if constraints is None:
        constraints = []
    if constraint_args is None:
        constraint_args = []
    n_az = gateset.shape[-2]
    n_rng = gateset.shape[-1]
    tmp_gateset = gateset.reshape((-1, n_az, n_rng))

    pia = np.zeros_like(tmp_gateset)

    a_used = np.empty(tmp_gateset.shape[:-1])
    b_used = np.empty(tmp_gateset.shape[:-1])

    # Calculate attenuation forward.
    # Indexing all rows of last dimension (radarbeams)
    beams2correct = np.where(np.ones(tmp_gateset.shape[:-1], dtype=np.bool_)) 
    # np.where(condition)返回满足条件的下标
    # tmp_gateset.shape[:-1] 去掉了最后一维
    small_sectors = np.zeros(tmp_gateset.shape[:-1], dtype=np.bool_)

    if n_a != 1:
        delta_a = (a_max - a_min) / (n_a - 1)
    else:
        delta_a = 0.0
    if n_b != 1:
        delta_b = (b_max - b_min) / (n_b - 1)
    else:
        delta_b = 0.0

    # Iterate over possible b-parameters
    for j in range(n_b):
        b = b_max - delta_b * j
        # Iterate over possible a-parameters
        for i in range(n_a):
            a = a_max - delta_a * i
            # Generate subset of beams that have to be corrected
            # tmp_gateset:(n_elev, n_az, n_gate)
            # sub_gateset::(n_elev * n_az, n_gate)
            sub_gateset = tmp_gateset[beams2correct] 
            sub_pia = calc_attenuation_forward(sub_gateset, a, b, gate_length) #正常使用HB计算PIA
            pia[beams2correct] = sub_pia
            a_used[beams2correct] = a
            b_used[beams2correct] = b
            # Indexing threshold exceeding beams
            # incorrectbeams: store beam index which exceeding all thresholds
            incorrectbeams = np.zeros(tmp_gateset.shape[:-1], dtype=np.bool_)
            for constraint, constraint_arg in zip(constraints, constraint_args):
                incorrectbeams = np.logical_or(
                    incorrectbeams, constraint(tmp_gateset, pia, *constraint_arg)
                )
            # Determine incorrect sectors larger than sector_thr
            large_sectors = _sector_filter(incorrectbeams, sector_thr)
            # Determine incorrect sectors smaller than sector_thr
            small_sectors = np.logical_or(
                small_sectors, (incorrectbeams & ~large_sectors)
            )
            beams2correct = np.where(large_sectors) #下一次迭代中需要计算PIA的坐标点。
            if len(pia[beams2correct]) == 0:
                break
        if len(pia[beams2correct]) == 0:
            break

    if np.any(small_sectors):
        # Interpolate reference pia of most distant
        # rangebin of invalid sectors.
        _interp_atten(pia, small_sectors)
        # Calculate attenuation forward by achieving reference
        # attenuation based on bisection-method.
        tmp_pia, tmp_a, tmp_b = bisect_reference_attenuation(
            tmp_gateset[small_sectors, :],
            pia[small_sectors, -1],
            a_max=a_max,
            a_min=a_min,
            b_start=b_max,
            gate_length=gate_length,
            mode="difference",
            thrs=0.25,
            max_iterations=10,
        )
        pia[small_sectors, :] = tmp_pia
        a_used[small_sectors] = tmp_a
        b_used[small_sectors] = tmp_b

    return pia.reshape(gateset.shape)

def pia_from_kdp(kdp, dr, gamma=0.08):
    """Retrieving path integrated attenuation from specific differential \
    phase (Kdp).
    The default value of gamma is based on :cite:`Carey2000`.
    Parameters
    ----------
    kdp : :class:`numpy:numpy.ndarray`
       array specific differential phase
       Range dimension must be the last dimension.
    dr : float
        gate length (km)
    gamma : float
       linear coefficient (default value: 0.08 for C band) in the relation between
       Kdp phase and specific attenuation (alpha)
       0.313 for X band
    Returns
    -------
    output : :class:`numpy:numpy.ndarray`
        array of same shape as kdp containing the path integrated attenuation
    """
    alpha = gamma * kdp
    pia = 2 * np.cumsum(alpha, axis=-1) * dr #进行了累加求和，即积分了
    return pia


def idecibel(x):
    """Calculates the inverse of input decibel values
    :math:`z=10^{x \\over 10}`
    Parameters
    ----------
    x : float or :class:`numpy:numpy.ndarray`
    Examples
    --------
    >>> from wradlib.trafo import idecibel
    >>> print(idecibel(10.))
    10.0
    """
    return 10.0 ** (x / 10.0)
