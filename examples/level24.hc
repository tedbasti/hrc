while(true) {
    a=input();
    b=input();
    while(a >= 0) {
        a = a - b;
    }
    if (a < 0) {
        a = a + b;
    }
    output(a);
}