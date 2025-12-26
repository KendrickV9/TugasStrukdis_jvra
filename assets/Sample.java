public class Sample {
	public static void main(String[] args) {
		int a = 1;
		int b = 2;
		int c = a + b;
		System.out.println(c);
	}
}

class Sample2 {
	public static void testMethod1(String[] args) {
		int a = 1;
		int b = 2;
		System.out.println(a + b);
	}

	class sampleInnerClass {
		public void testMethod1() {
			int a = 1;
			int b = 2;
			int c = 3;
		}
	}
}
