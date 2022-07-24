zero = 5;
while(true) {
    counter=zero;
    number=input();
    while(number >= 0) {
        counter = counter + number;
        number--;
    }
    output(counter);
}