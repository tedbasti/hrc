while(true) {
    a=input();
    if (a >= 0) {
        while( a >= 0) {
            output(a);
            a--;
        }
    } else {
        while( a != 0) {
            output(a);
            a++;
        }
        output(a);
    }
}