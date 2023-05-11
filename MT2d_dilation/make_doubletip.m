function XY = make_doubletip(radius_v, angle, tilt, ymax, N, dtx, dty)
  
  epsilon = angle(1)*pi/180;
  epsilon2 = angle(2)*pi/180;
  gamma = tilt*pi/180;
  
  radius = radius_v(1);
  radius2 = radius_v(2);
  
  xt = radius/sqrt(1+tan(epsilon/2)^2)
  H = radius/sqrt(1+tan(epsilon/2)^2)*(1/tan(epsilon/2) + tan(epsilon/2));
  
  xt2 = radius2/sqrt(1+tan(epsilon2/2)^2)
  H2 = radius2/sqrt(1+tan(epsilon2/2)^2)*(1/tan(epsilon2/2) + tan(epsilon2/2));
  
  h = H - radius;
  h2 = H2 - radius2;
  
  xmax = (ymax+h)*tan(epsilon/2);
  
  x = [-xmax:2*xmax/N:xmax]';
  
  RM = [cos(gamma),-sin(gamma);sin(gamma),cos(gamma)];
  
  y = abs(x/tan(epsilon/2));
  %y = k*x.^2;
  yr = -sqrt(radius^2 - x.^2) + H;
  
  y2 = dty + abs((x-dtx)/tan(epsilon2/2));
  yr2 = -sqrt(radius2^2 - (x-dtx).^2) + H2 + dty;
  
  tip = y;
  tip2 = y2;
  
  for i=1:N
    if (x(i) < -xt)
      tip(i) = y(i);
    elseif (x(i) > xt)
      tip(i) = y(i);
    else
      tip(i) = yr(i);
    endif
    
  endfor
  
  for i=1:N
    if (x(i) < -xt2+dtx)
      tip2(i) = y2(i);
    elseif (x(i) > xt2+dtx)
      tip2(i) = y2(i);
    else
      tip2(i) = yr2(i);
    endif
    
  endfor
  
  tip = tip-h; 
  tip2 = tip2-h2; 
  
  
  
  XY = [x,min([tip2,tip],[],2)];
  %XY = [x,tip];
  XY = (RM*XY')';
  XY(:,2) -= min(XY(:,2));
  
  %plot(XY(:,1),XY(:,2),'.m')
  %axis([-50,50,-10,50],"equal");
  %pause
endfunction
