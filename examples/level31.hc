counter=14;
temp=13;
while(true) {
    temp=input();
    if (temp != 0) {
        *counter = temp;
        counter++;
    } else {
        counter--;
        while(counter >= 0) {
            output(*counter);
            counter--;
        }
        counter++;
    }
}