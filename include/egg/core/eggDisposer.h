#ifndef EGG_DISPOSER_H
#define EGG_DISPOSER_H

#include <nw4r/ut/list.h>

namespace EGG
{

class Heap;

class Disposer
{
public:
    Disposer( );
    virtual ~Disposer( );

private:
    Heap *mHeap;
    nw4r::ut::Link mLink;
};
STATIC_ASSERT( sizeof( Disposer ) == 0x10 );

} // namespace EGG

#endif
