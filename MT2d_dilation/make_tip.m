function XY = make_tip(radius, angle, tilt, ymax, N)
  
  epsilon = angle*pi/180;
  gamma = tilt*pi/180;
  
  xt = radius/sqrt(1+tan(epsilon/2)^2)
  H = radius/sqrt(1+tan(epsilon/2)^2)*(1/tan(epsilon/2) + tan(epsilon/2));
  h = H - radius;
  
  xmax = (ymax+h)*tan(epsilon/2);
  
  x = [-xmax:2*xmax/N:xmax]';
  
  RM = [cos(gamma),-sin(gamma);sin(gamma),cos(gamma)];
  
  
  y = abs(x/tan(epsilon/2));
  yr = -sqrt(radius^2 - x.^2) + H;
  
  
  
  tip = y;
  
  for i=1:N
    if (x(i) < -xt)
      tip(i) = y(i);
    elseif (x(i) > xt)
      tip(i) = y(i);
    else
      tip(i) = yr(i);
    endif
    
  endfor
  
  tip = tip-h; 
  
  
  
  XY = [x,tip];
  XY = (RM*XY')';
  XY(:,2) -= min(XY(:,2));
  
  
  
  plot(XY(:,1),XY(:,2),'.m')
  axis([-50,50,-10,50],"equal");
  
endfunction
