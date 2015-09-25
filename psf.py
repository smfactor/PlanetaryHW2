import numpy as np
from scipy.ndimage import interpolation as intp
from astropy.io import fits
from astropy.io import ascii
import sys


files = ascii.read('NIRC2_sci_20020_1.txt')
fileNames = np.array(files['fileNames'])
targets = np.array(files['target'])

positions = ascii.read('starPositions.txt')
xref, yref = 512., 512.

ROXs42B = np.array([])
ROXs12 = np.array([])
n = np.size(targets)
for i in range(n):
    
    im = fits.getdata('calfits/'+fileNames[i])
    sim = intp.shift(im,[yref-positions['y'][i],xref-positions['x'][i]])
    if targets[i]==1:
        if ROXs42B.sum()==0:
            ROXs42B=np.array([sim])
        else:
            ROXs42B = np.append(ROXs42B,[sim],axis=0)
    if targets[i]==2:
        if ROXs12.sum()==0:
            ROXs12=np.array([sim])
        else:
            ROXs12 = np.append(ROXs12,[sim],axis=0)

    percent = float(i) / n
    hashes = '#' * int(round(percent * 20))
    spaces = ' ' * (20 - len(hashes))
    sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


sum42B = np.sum(ROXs42B,axis=0)
fits.writeto('ROXs42Bsum.fits',sum42B)
sum12 = np.sum(ROXs12,axis=0)
fits.writeto('ROXs12sum.fits',sum12)

med42B = np.median(ROXs42B,axis=0)
fits.writeto('ROXs42Bmed.fits',med42B)
med12 = np.median(ROXs12,axis=0)
fits.writeto('ROXs12med.fits',med12)
