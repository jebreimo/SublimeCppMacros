@
template <typename T>
long foo(T& bar);

@@
template <typename T>
long foo(T& bar,
         Foozle foo);

@<T>Foo<T, 3>
/* Comments
 */
long foo(T& bar);
