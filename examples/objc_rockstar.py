from rockstar import RockStar

objc_code = """#import <Foundation/Foundation.h>

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSLog(@"Hello World!");
    }
    return 0;
}"""

rock_it_bro = RockStar(days=400, file_name='helloWorld.m', code= objc_code)
rock_it_bro.make_me_a_rockstar()
