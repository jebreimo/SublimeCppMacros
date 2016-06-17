@
template <typename T>
long foo(T& bar);
@@
template <typename T>
long foo(T& bar,
         Foozle foo);

@<T>@<T, 3>
/* Comments
 */
long foo(T& bar);

@<T>@
virtual long foo(T& bar) const override;

virtual void foo(T& bar) const override;

template <typename U, typename V>
auto operator*(const Vector<U>& u, Vector<V>& v) -> decltype(u * v);

TestImpl& setFoo(const std::string& foo)
