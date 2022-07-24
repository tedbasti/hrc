zero=9;
while(true) {
    a=zero;
    a++;
    b=a;
    c=a+b;
    d=input();
    while (d >= a) { // Hallo Welt
        output(a);
        a=b;
        b=c;
        c=a+b;
    }
}