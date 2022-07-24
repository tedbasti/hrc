zero=9;
while(true) {
    a=input();
    b=input();
    counter=zero;
    while(a >= 0) {
        a = a - b;
        counter++;
    }
    if (a < 0) { counter--; }
    output(counter);
}