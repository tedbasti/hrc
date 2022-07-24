min=input();
while(true) {
    temp=input();
    if (temp != 0) {
        if (temp < min) {
            min = temp;
        }
    } else {
        output(min);
        min=input();
    }
}