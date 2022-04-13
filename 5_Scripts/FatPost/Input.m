%% Project: MHH Dissertation
%  Title/File: Input.m
%  Author: Bruno Luna 
%  Date (start): 23 Jun 2021
%
%  Content
%  ------------
% 
%  This file contains the input for calculation of a beam/frame
%  representing a dental implant in a (very) simplified
%  manner. All input data is transferred to main function as Octave structures.
%
%  Main assumptions:
%  1 - A titanium dental implant can be approximmated via a 1D cantilever beam.
%  2 - See calculation *.m files for specific assumptions.
%  3 - Base dimensions, base loads and materials as per Kitamura2004 article 
%      (see JabRef databank for thesis for more details).
%
function InpData = Input

%% Input values (only values to be changed manually by user!)
%% Pay (much) attention to consistent units!

% General input
nYear = 4;              % Total number of years(+1) to be considered (year)
n = linspace(0,nYear,nYear + 1); % Vector with periods to be considered (year)
np = 7;                          % Number of points to calculate beam (adim)
np = 2*floor(np/2)+1;   % Force a odd number of points (i.e., add one if needed)
Lw = 1.0;                        % Line weight for output graphics (admin)
Gen = struct("np", np, "Lw", Lw);

% Length of implant
Lini = 10;          % Initial length of beam (mm)
LAddFac = 0.5;      % Additive factor for beam in each step (mm)
LMultFac = 1.0;     % Multiplicative factor for beam in each step (adim)
L = (Lini + n*LAddFac).*LMultFac.^n; % Lengths vector, one for each year n (mm)
x = linspace(0,L,np);                % Points to calculate beam
Len = struct("L", L, "x", x);

% Cross-section of implant
dImp = 4;            % Diameter of implant (mm)
A = (pi*dImp^2)/4;   % Area (mm^2)
I = (pi*dImp^4)/64;  % Second moment of area (mm^4)
c = dImp/2;          % Distance of most outward fibers from neutral axis (mm)
Ks = 9/10;           % Shear correction factor (e.g. 9/10 for circular section)
CS = struct("A", A, "dImp", dImp, "I", I ,"c", c, "Ks", Ks);

% Material intrinsic properties
E = 110000; % Young modulus (N/mm^2 [MPa])
G = 40000;  % Shear modulus (N/mm^2 [MPa])
Mat = struct("E", E, "G", G);

% Load values and corresponding cycle qty (both must have the same length!)
P = [300];  % Value of point loads amplitude for each sub-step (N)
              % Buccolingually, i.e., perpendicular to beam
P = reshape(P,1,1,[]);  % Reshape of load vector to allow calculations           
nc = [10^4];  % Number of cycles for which a given load range is applied(adim)
nc = reshape(nc,1,1,[]); % Reshape of load vector to allow calculations
R = -1;     % Load ratio (Pmin/Pmax). -1 for reverse, 0 for zero based. (admin)
Kf = 1.21;   % Fatigue stress factor (lumps surface, concentration factors, etc.)

if (isequal(size(P),size(nc)) != 1)
  error("Input error: Loads vector length not equal to cycles vector length")
endif
Load = struct("P", P, "nc", nc, "R", R, "Kf", Kf);

% General input structure for rest of program
InpData = struct("Gen", Gen, "Len", Len, "CS", CS, "Mat", Mat, "Load", Load);
endfunction