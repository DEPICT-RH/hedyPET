import json
import numpy as np
from matplotlib import pyplot as plt
import os 

with open(f"{os.path.dirname(__file__)}/totalseg_ct_classes.json","r") as handle:
    TS_CLASS_TO_LABEL  = json.load(handle)


def plot_patplak(X,Y, slope, intercept, n_frames_regression):
    reg = lambda x: slope*x + intercept
    xs = np.array([np.nanmin(X),np.nanmax(X)])
    plt.vlines(X[-n_frames_regression],np.nanmin(Y),np.nanmax(Y),linestyle=':',color="k",alpha=0.5)
    plt.plot(xs,reg(xs),'k',linewidth=0.5,label=f"Ki={slope:.2E},b={intercept:.2E}")
    plt.plot(X,Y,'.r')

