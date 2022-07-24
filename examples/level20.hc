zero=9;
while (true) {
    a=input();
    b=input();
    c=zero;
    while (a != 0) {
        c = c + b;
        a--;
    }
    output(c);
}