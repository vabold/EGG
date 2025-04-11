#ifndef COMMON_H
#define COMMON_H

#ifndef NULL
#define NULL 0
#endif

typedef signed char s8;
typedef signed short s16;
typedef signed long s32;
typedef signed long long s64;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned long u32;
typedef unsigned long long u64;

typedef float f32;
typedef float f64;

typedef u32 size_t;
typedef u32 uintptr_t;

typedef int BOOL;
enum
{
    FALSE,
    TRUE
};

#ifdef __cplusplus
#define STATIC_ASSERT( cond ) __static_assert( cond, #cond )
#endif

#endif
