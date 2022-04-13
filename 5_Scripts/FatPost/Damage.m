%% Project: MHH Dissertation
%  Title/File: Damage.m
%  Author: Bruno Luna 
%  Date (start): 23 May 2021
%
%  Content
%  ------------
% 
%  This file contains code for calculation of damage on beam
%
%  Main assumptions:
%  1 - Constant cycle load (i.e., "sinus"-like load curve)
%  2 - SN curve with as a single segment (no "knee")
%  3 - All calculations valid for the input load range only
%  4 - Surely many others (model still VERY simplistic)
%

function OutData = Damage(InpData, Sbmax);
 
%% Setup the parameters used
nc = InpData.Load.nc; % Number of cycles for a load (adim)
R = InpData.Load.R;   % Load ratio (adim)

%% Calculations
Samp = Sbmax*(1-R)/2; % Convertion of max stress to stress amplitude as SN input
Ni = DamageJanececk2015(Samp);
D = nc./Ni;           % Damage by this load range and number of cycles (adim)

%% Check if failure due to fatigue occurred in most stressed point of beam
if (max(sum(D,3)) >= 1.0)
  disp("Fatigue failure occurred to implant!")
else
  disp("No fatigue failure occurred to implant!")
endif

%% Output data from this program
OutData = struct("Ni", Ni, "D", D);
endfunction

%% For testing/debugging only

%% Calculations
%% Setup the parameters used
##nc = InpData.Load.nc; % Number of cycles for a load range (adim)
##C = InpData.Mat.C;    % Fatigue capacity for SN curve (TO CHECK UNITS!)
##m = InpData.Mat.m;    % Exponent for SN curve (TO CHECK UNITS!)
##Ni = C./(Sbmax.^m);   % Endurable number of cycles from SN curve (# of cycles)