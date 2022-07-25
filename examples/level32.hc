zero=14;
chr=15;
pos=16;
counter=17;
while(true) {
    chr=input();
    pos=zero;
    counter=zero;
    while(*pos != 0) {
        if (*pos == chr) {
            counter++;
        }
        pos++;
    }
    output(counter);
}