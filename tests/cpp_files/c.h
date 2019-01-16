class A{
public:
    A();
    ~A();
    void ama();
    int aia();
    float afa();
};
    
namespace foo{
    class C{
    public:
        C();
        ~C();
        void ma();
        int ia();
        float fa();
    };
}

namespace bar{
    class D{
    public:
        D();
        ~D();
        void ma();
        int ia();
        float fa();
    };
}