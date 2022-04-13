%% Project: MHH Dissertation
%  Title/File: SimplySupBeam.m
%  Author: Bruno Luna 
%  Date (start): 22 May 2021
%
%  Content
%  ------------
% 
%  This file contains code for calculation of simply supported beam
%  with concentrated load at the center.
%
%  Main assumptions:
%  1 - Euler-Bernoulli conditions met
%  2 - Constant cross section
%  3 - Linear material (Hook law valid)
%

function M = SimplySupBeam(InpVec)
  
%% Setup the parameters used
L = InpVec(1);   % Length of beam (mm)
P = InpVec(2);   % Value of point load (N)
E = InpVec(3);   % Young modulus (N/mm^2 [MPa])
I = InpVec(4);   % Second moment of area (mm^4)
np = 10;       % Number of points to calculate beam (adim)

%% Setup auxiliary vectors/values
np = 2*floor(np/2)+1; % Force a odd number of points (i.e., add one if needed)
x = linspace(0,L,np);    % Points to calculate beam
x1 = x<=(L/2);           % First half of beam
x2 = x>(L/2) & x<=L;     % Second half of beam
d = zeros(1,length(x));  % Initialize deflection vector 
s = zeros(1,length(x));  % Initialize slope vector 
M = zeros(1,length(x));  % Initialize moment vector 
V = zeros(1,length(x));  % Initialize shear force vector 

%% Calculations
% Max values
R = P/2;                  % Reaction forces (N)
dmax = -(P*L^3)/(48*E*I); % Maximum deflection (mm)
smax = -(P*L^2)/(16*E*I); % Maximum slope (rad)
Mmax = (P*L)/4;           % Maximum moment (N*mm)
Vmax = P/2;               % Maximum shear force (N)
% Function along beam
d1 = -((P*x(x1))/(48*E*I)).*(3*L^2-4*x(x1).^2); % Def. for first half of beam
d = cat(2, d1, flip(d1(1:end-1)));    % Def. along beam(mm)
s1 = -(P/(16*E*I)).*(L^2-4*x(x1).^2); % Slope for first half of beam 
s = cat(2, s1, -flip(s1(1:end-1)));   % Slope along beam (rad)
M1 = -(P*x(x1))/2;                    % Moment for first half of beam 
M = cat(2, M1, flip(M1(1:end-1)));    % Moment along beam (N*mm)
V1 = -P/2*ones(1,length(x(x1)));      % Shear for first half of beam 
V =  cat(2, V1, -flip(V1(1:end-1)));  % Shear along beam(N) 

%% Plot results
subplot (2, 2, 1)
plot (x, d, "k", "linewidth", 2.0);
xlabel ("x (mm)");
ylabel ("d(x) (mm)");
title ("Deflection");
subplot (2, 2, 2)
plot (x, s, "m", "linewidth", 2.0);
xlabel ("x (mm)");
ylabel ("s(x) (rad)");
title ("Slope");
subplot (2, 2, 3)
plot (x, M, "r", "linewidth", 2.0);
xlabel ("x (mm)");
ylabel ("M(x) (N*mm)");
title ("Moment");
subplot (2, 2, 4)
plot (x, V, "b", "linewidth", 2.0);
xlabel ("x (mm)");
ylabel ("V(x) (N)");
title ("Shear force");
endfunction