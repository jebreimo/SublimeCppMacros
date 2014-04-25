    size_t m_Assertions;
    std::vector<Error> m_Errors;
    std::string m_Name;
    std::unique_ptr<Time> m_StartTime;
    std::vector<std::pair<std::string, std::string>> m_Filter;

@<T, int N>@@
    std::vector<Error> m_Errors;
    std::string m_Name;
@Fjon
    clock_t m_StartTime;
@<T, int K>@@
    clock_t m_EndTime;
@<T>@@<T, Foo::UserId>
    std::vector<Error> m_Errors;
    std::string m_Name;


@<T><T, Foo::UserId>
    size_t m_Assertions;

@<T>@<T, Foo::UserId>
    size_t m_Assertions;
