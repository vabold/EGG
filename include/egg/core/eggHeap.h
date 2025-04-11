#ifndef EGG_HEAP_H
#define EGG_HEAP_H

#include <egg/core/eggDisposer.h>

/* ================================================================ *
 *     CHANGELOG
 * ----------------------------------------------------------------
 *
 * - 2011/11: Removed mParentHeap
 *
 * ================================================================ */

namespace EGG
{

class Heap
{
public:
    void appendDisposer( Disposer *disposer )
    {
        nw4r::ut::List_Append( &mChildren, disposer );
    }

    void removeDisposer( Disposer *disposer )
    {
        nw4r::ut::List_Remove( &mChildren, disposer );
    }

    static Heap *findContainHeap( const void *memBlock );

private:
#if EGG_VERSION >= 201111L
    u8 _00[ 0x24 - 0x00 ];
    nw4r::ut::List mChildren;
    u8 _30[ 0x34 - 0x30 ];
#else
    u8 _00[ 0x28 - 0x00 ];
    nw4r::ut::List mChildren;
    u8 _34[ 0x38 - 0x34 ];
#endif
};

#if EGG_VERSION >= 201111L
STATIC_ASSERT( sizeof( Heap ) == 0x34 );
#else
STATIC_ASSERT( sizeof( Heap ) == 0x38 );
#endif

} // namespace EGG

#endif
