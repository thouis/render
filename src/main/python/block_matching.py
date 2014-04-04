import numpy as np
import cv2
import sys
import scipy.ndimage as nd
from collections import defaultdict

Debug = False

# Reimplementation of matchByMaximalPMCC
# https://github.com/axtimwalde/mpicbg/blob/master/mpicbg/src/main/java/mpicbg/ij/blockmatching/BlockMatching.java
#
# assume, for now, that the two images being matched are roughly aligned

neighbors = np.ones((3, 3), dtype=np.bool)

def derivs(im):
    '''Derivatives in a 3x3 window'''
    di = (im[2, 1] - im[0, 1]) / 2.0
    dj = (im[1, 2] - im[1, 0]) / 2.0
    dii = (im[0, 1] - 2 * im[1, 1] + im[2, 1])
    djj = (im[1, 0] - 2 * im[1, 1] + im[1, 2])
    dij = (im[2, 2] - im[2, 0] - im[0, 2] + im[0, 0]) / 4.0
    return di, dj, dii, djj, dij

# for monitoring/debugging results of block matching
matching_results = defaultdict(int)

def match_block(src_block, dest_block,
                min_NCC_thresh=0.7,  # defaults taken from BlockMatching.java code
                min_ratio_second_best=0.9,
                max_curvature=10.0):
    ncc = cv2.matchTemplate(dest_block, src_block, cv2.TM_CCOEFF_NORMED)

    # check min correlation coefficient threshold

    if Debug:
        cv2.imshow("template", src_block)
        cv2.imshow("dest", dest_block)
        tmpncc = (ncc + 1.0) / 2.0
        cv2.imshow("ncc", tmpncc)
        cv2.waitKey(0)

    if ncc.max() < min_NCC_thresh:
        matching_results['low NCC'] += 1
        return None

    # find local maxima
    maxima_values = np.sort(ncc[ncc == nd.filters.maximum_filter(ncc, footprint=neighbors, mode='nearest')])[::-1]

    # Check that either there's only one local maximum, or that the best value
    # is significantly better than the second best.
    if len(maxima_values) > 1:
        ratio = (maxima_values[0] + 1) / (maxima_values[1] + 1)
        if ratio < min_ratio_second_best:
            matching_results['maximum not unique'] += 1
            return None

    # find location of maximum
    imax, jmax = np.unravel_index(np.argmax(ncc), ncc.shape)

    # check that it's not at the edge
    if (imax == 1) or (jmax == 1) or (imax == ncc.shape[0] - 1) or (jmax == ncc.shape[1] - 1):
        matching_results['at edge'] += 1
        return None

    # compute derivatives
    di, dj, dii, djj, dij = derivs(ncc[imax-1:imax+2, jmax-1:jmax+2])

    # check localization
    det = dii * djj - dij * dij
    trace = dii + dij
    if det <= 0 or (trace * trace / det > max_curvature):
        matching_results['poor localization by det/trace'] += 1
        return None

    # localize by Taylor expansion
    # invert Hessian
    inv_ij = -dij / det
    inv_ii = djj / det
    inv_jj = dii / det
    off_i = -inv_ii * di - inv_ij * dj
    off_j = -inv_jj * dj - inv_ij * di
    if abs(off_i) >= 1 or abs(off_j) >= 1:
        matching_results['poor localization by Taylor expansion'] += 1
        return None

    matching_results['good match'] += 1
    return (imax + off_i, jmax + off_j)

def subim(im, ci, cj, radius):
    if (ci - radius < 0) or (cj - radius < 0) or \
            (ci + radius >= im.shape[0]) or (cj + radius >= im.shape[1]):
        raise IndexError()
    return im[ci-radius:ci+radius+1, cj-radius:cj+radius+1]

def match_mesh(image1, image2, grid_step, template_radius, search_radius):
    # sample at equilateral triangles
    dj = grid_step
    di = int(np.ceil(np.sqrt(3.0 * grid_step / 4.0)))

    for idx, i in enumerate(range(0, image1.shape[0], di)):
        j_offset = (dj / 2) if (idx & 1) else 0
        for j in range(j_offset, image1.shape[1], dj):
            try:
                match = match_block(subim(image1, i, j, template_radius),
                                    subim(image2, i, j, search_radius))
                if match:
                    if Debug:
                        cv2.imshow("im1", subim(image1, i, j, template_radius).astype(np.uint8))
                        cv2.imshow("im2", subim(image2,
                                                match[0] + i + template_radius - search_radius,
                                                match[1] + j + template_radius - search_radius,
                                                template_radius).astype(np.uint8))
                        cv2.waitKey(0)
                    yield (i, j), (match[0] + i - search_radius, match[1] + j - search_radius)
            except IndexError:
                pass


if __name__ == '__main__':
    # TrakEM2 code does the following, as far as I can tell:
    # - scale src/dest by some factor (scale)
    # - normalize contrast: min/max to 0/1
    # - match points using matchByMaximalPMCC
    im1 = cv2.imread(sys.argv[1])[:, :, 0]
    im2 = cv2.imread(sys.argv[2])[:, :, 0]
    matches = [m for m in match_mesh(im1, im2, 50, 25, 200)]
    for m in matches:
        (si, sj), (ti, tj) = m
        print si, sj, "to", ti, tj
    sys.stderr.write("Matching results\n")
    for cause, count in matching_results.iteritems():
        sys.stderr.write("    %s %s\n" % (cause, count))
