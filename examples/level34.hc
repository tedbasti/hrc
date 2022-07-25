zero=5;
pos=6;
chr=7;
while(true) {
    pos = zero;
    chr = input();
    while(*pos != 0) {
        if (*pos == chr) {
            pos = zero;
            chr = input();
        } else {
            pos++;
        }
    }
    output(chr);
}