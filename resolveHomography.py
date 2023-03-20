import numpy as np



def resolveHomography(pts_src, pts_dst) :
    
    pts_src = list(map(
        lambda x : np.squeeze(x),
        np.split(pts_src, 4)
    ))
    pts_dst = list(map(
        lambda x : np.squeeze(x),
        np.split(pts_dst, 4)
    ))
    zeros = np.zeros(3)

    P = np.vstack(list(map(
        lambda p_src, p_dst : np.stack(
            (
                np.concatenate((p_src*-1, zeros, p_src*p_dst[0])),
                np.concatenate((zeros, p_src*-1, p_src*p_dst[1]))
            )
        ),
        pts_src, pts_dst
    )))

    [U, S, Vt] = np.linalg.svd(P)
    homography = Vt[-1].reshape(3, 3)
    return homography / homography[2][2]


def resolveHomography(pts_src, pts_dst) :
    
    pts_src = list(map(
        lambda x : np.squeeze(x),
        np.split(pts_src, 4)
    ))
    pts_dst = list(map(
        lambda x : np.squeeze(x),
        np.split(pts_dst, 4)
    ))
    zeros = np.zeros(3)

    P = np.vstack(list(map(
        lambda p_src, p_dst : np.stack(
            (
                np.concatenate((p_src*-1, zeros, p_src*p_dst[0])),
                np.concatenate((zeros, p_src*-1, p_src*p_dst[1]))
            )
        ),
        pts_src, pts_dst
    )))
    
    vector = np.zeros(9)
    vector[8] = 1

    P = np.vstack((P, vector))

    return np.matmul(
        np.linalg.inv(P),
        vector.reshape(9, 1)
    )

    [U, S, Vt] = np.linalg.svd(P)
    homography = Vt[-1].reshape(3, 3)
    return homography / homography[2][2]