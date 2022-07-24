while(true) {
    a = input();
    b = input();
    c = input();
    zero = a - a;
    three = zero;
    three++; three++; three++;
    counter = zero;
    while(counter < three) {
        if(b < a){
            tmp = b;
            b = a;
            a = tmp;    
        }

        if(c < b){
            tmp = c;
            c = b;
            b = tmp;
        }
    }
    output(a);
    output(b);
    output(c);
}