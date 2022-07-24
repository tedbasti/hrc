while(true) {
    a=input();
    b=input();
    c=input();
    if (b < a) {
        temp = b;
        b = a;
        a = temp;
    }
    if (c < b) {
        temp = c;
        c = b;
        b = temp;
    }
    if (b < a) {
        temp = b;
        b = a;
        a = temp;
    }
    output(a);
    output(b);
    output(c);
}