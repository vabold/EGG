#ifndef NW4R_UT_LIST_H
#define NW4R_UT_LIST_H

#include <Common.h>

namespace nw4r
{
namespace ut
{

struct List
{
    void *headObject;
    void *tailObject;
    u16 numObjects;
    u16 offset;
};

struct Link
{
    void *prevObject;
    void *nextObject;
};

void List_Append( List *list, void *object );
void List_Remove( List *list, void *object );

} // namespace ut
} // namespace nw4r

#endif
