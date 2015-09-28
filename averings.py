import numpy as np
import scipy.interpolate as intp
from astropy.io import fits
from astropy.io import ascii
import sys

print 'subtracting average radial profile'

files = ascii.read('NIRC2_sci_20020_1.txt')
fileNames = np.array(files['fileNames'])
targets = np.array(files['target'])

o = 512

n = np.size(targets)
for i in range(n):
    if targets[i]!=0:
        im = fits.getdata('results/'+fileNames[i][:-5]+'.reg.fits')

        smooth = intp.RectBivariateSpline(range(1024),range(1024),im)

        R = np.arange(300)
        theta = np.arange(360)

        f = np.zeros((300,360))
        for r in R:
            for t in theta:
                trad = np.radians(t)
                xp = o + r*np.cos(trad)
                yp = o + r*np.sin(trad)
                f[r,t] = smooth(yp,xp)

        f = np.median(f, axis=1)
        
        smoothf = intp.interp1d(R,f,bounds_error=False,fill_value=0.0)
        xp, yp = np.arange(1024),np.arange(1024)
        xg, yg = np.meshgrid(xp,yp)
        rp = np.sqrt((xg-o)**2 + (yg-o)**2)

        imsub = im - smoothf(rp)

        fits.writeto('results/'+fileNames[i][:-5]+'.ringsub.fits',imsub)

        percent = float(i) / n
        hashes = '#' * int(round(percent * 20))
        spaces = ' ' * (20 - len(hashes))
        sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
        sys.stdout.flush()
sys.stdout.write("\n")
