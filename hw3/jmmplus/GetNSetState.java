import java.util.concurrent.atomic.AtomicIntegerArray;

class GetNSetState implements State{
	private AtomicIntegerArray value;
    private byte maxval;

    private int[] getIntArray(byte[] v){
    	int[] intArray = new int[v.length];
    	for(int i = 0; i < v.length; i++){
    		intArray[i]=v[i];
    	}
    	return intArray;
    }

    GetNSetState(byte v[]) { value = new AtomicIntegerArray(getIntArray(v)); maxval = 127; }
    GetNSetState(byte v[], byte m) { value = new AtomicIntegerArray(getIntArray(v)); maxval = m; }

    public int size() { return value.length(); }

    public byte[] current() {
    	byte[] temp = new byte[value.length()];
    	for(int i = 0; i<value.length(); i++){
    		temp[i] = (byte)value.get(i);
    	}
    	return temp;
    }

    public boolean swap(int i, int j) {
    int a = value.get(i);
    int b = value.get(j);
	if (a <= 0 || b >= maxval) {
	    return false;
	}
	value.set(i,--a);
	value.set(j,++b);
	return true;
    }
}