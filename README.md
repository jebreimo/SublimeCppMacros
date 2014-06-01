SublimeCppMacros
================

C++ macros for Sublime Text.

There are currently three macros:

* C++: Declare getter/setter
* C++: Implement getter/setter
* C++: Implement function

All three macros takes in one or more lines of code and transform them into new lines of code.

C++: Declare getter/setter
--------------------------
Input is a member variable declaration, output are declarations of get and set functions for the variable. The variable name must start with "m_", and the whole declaration must appear on a single line. Multiple lines with declarations can be transformed at once. 

###Example:

Assuming the class contains the lines:

    int m_IntegerValue;
    Foozle m_ParentFoozle;

Copy the lines and paste them where the get and set functions should be inserted in the code. Select them, open the command palette and run the "C++: Declare getter/setter" command. The lines will be replaced by:

    int integerValue() const;
    void setIntegerValue(int value);

    const Foozle& parentFoozle() const;
    void setParentFoozle(const Foozle& value);

C++: Implement getter/setter
----------------------------
Input is a member variable declaration, output are implementations of get and set functions for the variable. The variable name must start with "m_", and the whole declaration must appear on a single line. Multiple lines with declarations can be transformed at once. 

###Example:

Assuming the class contains the lines:

    int m_IntegerValue;
    Foozle m_ParentFoozle;

Copy the lines and paste them where the get and set functions should be inserted in the code. Select them, open the command palette and run the "C++: Implement getter/setter" command. The lines will be replaced by:

    int FileName::integerValue() const
    {
        return m_IntegerValue;
    }

    void FileName::setIntegerValue(int value)
    {
        m_IntegerValue = value;
    }

    const Foozle& FileName::parentFoozle() const
    {
        return m_ParentFoozle;
    }

    void setParentFoozle(const Foozle& value)
    {
        m_ParentFoozle = value;
    }

C++: Implement function
-----------------------
Input is a function declaration, output is an implementation of the function with class name prefix (and, potentially, template parameters) of get and set functions for the variable. A single function declaration can consist of multiple lines. Multiple declarations can be transformed at once.

###Example:

Assuming you have the following function declarations:

    std::string processFoo(int n);

    template <typename T>
    Foozle processBar(double d,
                      const T& bar);

Copy the lines and paste them where the implementation should be inserted. Select them, open the command palette and run the "C++: Implement function" command. The lines will be replaced by:

    std::string FileName::processFoo(int n)
    {
        return std::string();
    }

    template <typename T>
    Foozle FileName::processBar(double d,
                                const T& bar)
    {
        return Foozle();
    }

Changing the class name and specifying template parameters
---------------------------------------------------------
This applies to both the "implement get/set" and "implement function" commands.

By default, the class name is the name of the current file without extension. It is possible to override this name or specify template arguments by inserting special lines in front of the lines to be expanded. The format of these lines are:

    "@" ("<" template-parameter ("," template-parameter)* ">")? ("@" | "@@" | class-name ("<" template-parameter ("," template-parameter)* ">")? )?

Once the class name or template parameters have been specified in a file, these are remembered and re-used on subsequent executions of the same command in the same file until another set of names and parameters are specified, or the application is closed.

###Example 1:
Implement a non-class function:

Input is:

    @
    std::string processFoo(int n);

Output is 

    std::string processFoo(int n)
    {
        return std::string();
    }
    
###Example 2:
Specify a class name different from the file name:

Input is:

    @TheClass
    std::string processFoo(int n);

Output is 

    std::string TheClass::processFoo(int n)
    {
        return std::string();
    }

###Example 3:
Use the current file name as class name, but add two template parameters to the class.

Input is:

    @<T, int N>@
    std::string processFoo(int n);

Output is:

    template <typename T, int N>
    const std::string& FileName<T, N>::processFoo() const;
