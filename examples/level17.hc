zero=4;
one=5;
while(true) {
    a=input();
    b=input();
    if (a<0) {
        if (b<0) {
            output(zero);
        } else {
            output(one);
        }
    } else {
        if (b<0) {
            output(one);
        } else {
            output(zero);
        }
    }
}