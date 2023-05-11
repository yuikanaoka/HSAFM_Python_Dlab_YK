function XY = make_mt(rMT,nPF)
  
  alpha = pi*(360/nPF)/180;
  R = rMT/(1+sin(alpha/2));
  
  xm = 0;
  ym = -R;
  r = R*sin(alpha/2)
  
  XY1 = circle_pf(xm,ym,r,1000);
  
  L=length(XY1);
  
  XY = zeros(nPF*L,2);
  
  RM = [cos(alpha),-sin(alpha);sin(alpha),cos(alpha)];
  
  XY(1:L,:) = XY1;
  
  #xm = 0;
  #ym = -10;
  #R = 5;
  #XY2 = circle_pf(xm,ym,R);
  
  XYn = XY1;
  
  for i=1:nPF-1
    
    XYn = (RM*XYn')';
    XY(L*i+1:L*(i+1),:) = XYn;
    
  endfor
  
  XY += [0,rMT];
  
  
  
endfunction
