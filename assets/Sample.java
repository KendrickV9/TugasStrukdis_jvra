public class Sample {
	public static void main(String[] args) {
		int a = 1;
		int b = 2;
		int c = a + b;
		int d = a + b;
		if (true) {
			int foo = 3;
			foo = foo + 1;
		}

		Point p = new Point(1, 2);
		System.out.println(c);
		System.out.println(d);
		System.out.println(p);
	}
}

class Point {
	public int x;
	public int y;

	public Point(int x, int y) {
		this.x = x;
		this.y = y;
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
