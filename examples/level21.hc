zero=5;
counter=zero;
while(true) {
    temp=input();
    if (temp == 0) {
        output(counter);
        counter=zero;
    } else {
        counter = counter + temp;
    }
}